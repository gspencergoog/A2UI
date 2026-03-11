import requests, json
payload = {
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
        "message": {"messageId": "req-1", "role": "user", "parts": [{"text": "Find me 2 chinese restaurants in SF."}]},
        "context": {"extensions": [{"uri": "https://a2ui.org/specification/v0_9/basic_catalog.json"}]}
    },
    "id": 1
}
res = requests.post("http://localhost:10002/", json=payload, stream=True)
for line in res.iter_lines():
    print(line.decode('utf-8'))
