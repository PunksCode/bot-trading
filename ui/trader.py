from .models import Portfolio, SystemState, ActiveOrder, TradeHistory
import pandas as pd

try:
    # Intenta importar tu cerebro real (que NO subirás)
    from .decision_engine_private import DecisionEngine
    print("🔓 CARGANDO MOTOR PROPIETARIO V11")
except ImportError:
    # Si no existe, carga la versión pública
    from .decision_engine import DecisionEngine
    print("🔒 CARGANDO MOTOR DEMO (PUBLICO)")

# CONFIGURACIONES
GRID_LINES = 10
SHANNON_THRESHOLD = 0.02 # 2% desvío

def ejecutar_sistema(df_4h, precio_actual):
    wallet, _ = Portfolio.objects.get_or_create(id=1)
    state, _ = SystemState.objects.get_or_create(id=1)
    engine = DecisionEngine(df_4h)
    
    # 1. ¿QUÉ DICE EL MERCADO AHORA?
    detected_regime, detected_strategy, reason = engine.detectar_regimen()
    
    log_msg = ""
    switch_occurred = False

    # 2. LÓGICA DE PERSISTENCIA (HISTERESIS)
    if detected_regime == state.current_regime:
        # El mercado sigue igual, reseteamos contadores de cambio
        state.pending_regime = 'NONE'
        state.confirmation_count = 0
        
    else:
        # El mercado sugiere un cambio...
        if state.pending_regime != detected_regime:
            # Es la primera vez que lo vemos
            state.pending_regime = detected_regime
            state.confirmation_count = 1
            log_msg += f"⏳ Posible cambio a {detected_regime} detectado (1/3). Esperando... "
        else:
            # Ya lo habíamos visto, sumamos confianza
            state.confirmation_count += 1
            log_msg += f"⏳ Confirmando {detected_regime} ({state.confirmation_count}/3)... "
            
            # SI LLEGAMOS A 3 CONFIRMACIONES -> CAMBIO REAL
            if state.confirmation_count >= 3:
                log_msg += f"🔄 CAMBIO CONFIRMADO: {state.current_regime} -> {detected_regime}. "
                
                # LIMPIEZA DE ESTRATEGIA ANTERIOR
                if state.active_strategy == 'GRID_V11':
                    ActiveOrder.objects.all().delete()
                    
                # APLICAR NUEVO ESTADO
                state.current_regime = detected_regime
                state.active_strategy = detected_strategy
                state.pending_regime = 'NONE'
                state.confirmation_count = 0
                switch_occurred = True

    # 3. ACTUALIZAR MÉTRICAS DE RIESGO (Drawdown)
    equity_actual = wallet.usdt_balance + (wallet.btc_balance * precio_actual)
    
    # High Watermark (Pico histórico)
    if equity_actual > state.peak_equity:
        state.peak_equity = equity_actual
        
    # Drawdown Actual %
    dd_actual = ((equity_actual - state.peak_equity) / state.peak_equity) * 100
    
    # Max Drawdown Histórico
    if dd_actual < state.max_drawdown:
        state.max_drawdown = dd_actual

    state.save()

    # 4. EJECUTAR ESTRATEGIA (Solo si no estamos cambiando justo ahora)
    if not switch_occurred:
        if state.active_strategy == 'GRID_V11':
            res = ejecutar_logic_grid(wallet, precio_actual, engine)
            log_msg += res
        elif state.active_strategy == 'SHANNON_V13':
            res = ejecutar_logic_shannon(wallet, precio_actual)
            log_msg += res
        else:
            log_msg += "Modo Cash/Hold activo."

    # Retorno para Dashboard
    return {
        "regime": state.current_regime,
        "strategy": state.active_strategy,
        "message": log_msg,
        "equity": round(equity_actual, 2),
        "dd": round(dd_actual, 2),          # Nueva métrica para UI
        "max_dd": round(state.max_drawdown, 2), # Nueva métrica para UI
        "usdt": round(wallet.usdt_balance, 2),
        "btc": round(wallet.btc_balance, 4)
    }

# =====================================================
# LÓGICA V11: GRID (ACUMULACIÓN / RANGO)
# =====================================================
def ejecutar_logic_grid(wallet, price, engine):
    orders = ActiveOrder.objects.all()
    
    # 1. SI NO HAY ÓRDENES -> INICIALIZAR
    if not orders.exists():
        lower, upper = engine.get_grid_params()
        step = (upper - lower) / GRID_LINES
        monto_usdt = (wallet.usdt_balance * 0.5) / (GRID_LINES / 2) # Usamos 50% capital
        
        # Crear parrilla
        import numpy as np
        grids = np.linspace(lower, upper, GRID_LINES)
        
        count = 0
        for level in grids:
            if level < price: # Abajo = Compra
                ActiveOrder.objects.create(price=level, amount_usdt=monto_usdt, side='BUY')
                count += 1
            elif level > price: # Arriba = Venta
                ActiveOrder.objects.create(price=level, amount_usdt=monto_usdt, side='SELL')
                count += 1
        return f"Grid Iniciado ({count} niveles). "

    # 2. MONITOREAR ÓRDENES
    msg = ""
    step = (orders.order_by('price')[1].price - orders.order_by('price')[0].price) if len(orders) > 1 else 0
    
    for order in orders:
        # HIT DE COMPRA
        if order.side == 'BUY' and price <= order.price:
            if wallet.usdt_balance >= order.amount_usdt:
                wallet.usdt_balance -= order.amount_usdt
                btc_bought = order.amount_usdt / order.price
                wallet.btc_balance += btc_bought
                
                # Pivotar a Venta
                new_price = order.price + step
                order.price = new_price
                order.side = 'SELL'
                order.save()
                
                TradeHistory.objects.create(strategy_used='GRID', action='ARBITRAGE_BUY', pnl_realized=0)
                msg = "♻️ Grid Arbitrage (Compra). "
        
        # HIT DE VENTA
        elif order.side == 'SELL' and price >= order.price:
            btc_needed = order.amount_usdt / (order.price - step)
            if wallet.btc_balance >= btc_needed:
                wallet.btc_balance -= btc_needed
                usdt_back = btc_needed * order.price
                wallet.usdt_balance += usdt_back
                
                profit = usdt_back - order.amount_usdt
                
                # Pivotar a Compra
                new_price = order.price - step
                order.price = new_price
                order.side = 'BUY'
                order.save()
                
                TradeHistory.objects.create(strategy_used='GRID', action='ARBITRAGE_SELL', pnl_realized=profit)
                msg = f"💰 Grid Profit (+${round(profit,2)}). "
                
    wallet.save()
    return msg if msg else "Grid Activo (Esperando cruce)..."

# =====================================================
# LÓGICA V13: SHANNON (PROTECCIÓN / INCERTIDUMBRE)
# =====================================================
def ejecutar_logic_shannon(wallet, price):
    # Valor total
    val_btc = wallet.btc_balance * price
    val_usdt = wallet.usdt_balance
    total = val_btc + val_usdt
    
    if total == 0: return "Sin Capital."

    # Peso actual
    weight_btc = val_btc / total
    diff = weight_btc - 0.50
    
    # Si el desvío es mayor al umbral (2%)
    if abs(diff) > SHANNON_THRESHOLD:
        target_btc_val = total * 0.5
        
        if diff > 0: # Sobra BTC -> VENDER
            usd_to_gain = val_btc - target_btc_val
            btc_to_sell = usd_to_gain / price
            
            wallet.btc_balance -= btc_to_sell
            wallet.usdt_balance += usd_to_gain
            action = "SHANNON_SELL"
            
        else: # Falta BTC -> COMPRAR
            usd_to_spend = target_btc_val - val_btc
            btc_to_buy = usd_to_spend / price
            
            wallet.usdt_balance -= usd_to_spend
            wallet.btc_balance += btc_to_buy
            action = "SHANNON_BUY"
            
        wallet.save()
        TradeHistory.objects.create(strategy_used='SHANNON', action=action)
        return f"⚖️ Rebalanceo Ejecutado ({action})."
    
    return "Shannon Balanceado (50/50)."