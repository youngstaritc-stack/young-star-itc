def process_incoming_mt5_data(data):
    return {"status": "received", "symbol": data.get("symbol")}
