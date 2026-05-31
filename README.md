# BTC Arbitrage Monitor: Real-Time Detection & Simulation

Este proyecto es un sistema de arbitraje de criptomonedas (BTC/USDT) entre Binance y Coinbase, diseñado para la detección y simulación de oportunidades en tiempo real con latencia mínima.

## 🚀 Arquitectura del Sistema

El sistema sigue una arquitectura en capas diseñada para la escalabilidad y la eficiencia:

1.  **Capa de Datos (WebSockets + CCXT):** Conexión directa a los streams de profundidad (OrderBook) de Binance y Coinbase para obtener actualizaciones cada 100ms.
2.  **Motor de Detección (Python Asyncio):** Procesa los orderbooks en memoria para identificar spreads rentables entre exchanges.
3.  **Capa de Cálculo (Profit Neto):** Aplica comisiones reales (taker fees), slippage estimado por niveles de profundidad y tarifas de retiro para calcular la rentabilidad neta real.
4.  **Capa de Ejecución (Simulada):** Gestión de carteras virtuales con balances iniciales, actualizando saldos y registrando P&L tras cada operación.
5.  **API & Push (FastAPI + WebSockets):** Expone endpoints REST para el historial y un canal WebSocket para enviar actualizaciones en tiempo real al frontend.
6.  **Interfaz (React + Vite):** Dashboard moderno con monitoreo de orderbooks, feed de oportunidades, historial de trades y gráfica de P&L acumulado.

## 🛠️ Tecnologías Utilizadas

*   **Backend:** Python 3.10+, FastAPI, Asyncio, WebSockets, SQLAlchemy (AioSqlite), Pydantic.
*   **Frontend:** React 18, Vite, Tailwind CSS, Recharts (gráficas), Lucide (iconos).
*   **Infraestructura:** Railway (Backend), Vercel (Frontend).

## 📈 Decisiones Técnicas Relevantes

*   **Asyncio Puro:** Se evitó el polling para reducir la latencia. El sistema reacciona instantáneamente a cada evento enviado por los exchanges.
*   **Circuit Breaker:** Implementación de gestión de riesgos que detiene el bot si el drawdown supera el 5% o si se detecta volatilidad extrema.
*   **Cálculo de Slippage:** A diferencia de otros bots que solo miran el mejor precio, este sistema consume niveles del orderbook hasta cubrir el volumen deseado, proporcionando un cálculo de profit mucho más realista.
*   **Gestión de Reconexión:** Los clientes de WebSockets incluyen lógica de "exponential backoff" para garantizar que el sistema se recupere automáticamente ante micro-cortes de red.

## 📋 Requisitos Previos

*   Python 3.10 o superior.
*   Node.js 18 o superior.
*   NPM o Yarn.

## 💻 Instalación y Uso Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/4liyat/arbitrage_system.git
cd arbitrage_system
```

### 2. Configurar el Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 3. Configurar el Frontend
En otra terminal:
```bash
cd frontend
npm install
npm run dev
```
La aplicación estará disponible en `http://localhost:5173`.

## ⚙️ Configuración (backend/config.py)

Puedes ajustar los siguientes parámetros:
*   `MIN_NET_PROFIT_PCT`: Beneficio neto mínimo (ej. 0.0015 para 0.15%).
*   `TRADE_VOLUME_BTC`: Volumen de la operación simulada (ej. 0.01 BTC).
*   `EXCHANGES`: Configuración de fees y slippage por exchange.

## 📄 Evaluación Técnica
Este sistema fue construido siguiendo estrictos estándares de calidad:
*   **Velocidad:** Detección en el mismo ciclo de evento del update del orderbook.
*   **Robustez:** Manejo de excepciones y reconexión automática.
*   **Calidad de Código:** Tipado estricto con Pydantic y separación clara de responsabilidades.

---
Desarrollado para el hackathon de arbitraje cripto.
ento del update del orderbook.
*   **Robustez:** Manejo de excepciones y reconexión automática.
*   **Calidad de Código:** Tipado estricto con Pydantic y separación clara de responsabilidades.

---
Desarrollado para el hackathon de arbitraje cripto.
