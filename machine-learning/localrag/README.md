
Attempt to reproduce https://jamwithai.substack.com/p/build-a-local-llm-based-rag-system?triedRedirect=true

## Setup

```shell
./setup.sh
```

## Run Tests

```shell
pytest test_integration.py
```

## Run Backend

```shell
./run.sh
```

## Run Frontend

```shell
streamlit run index.py
```

## Test Backend

```shell
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt":"Why is the sky blue?"
}'
```