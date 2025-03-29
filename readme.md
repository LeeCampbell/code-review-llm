Run the model in a container
https://blog.xeynergy.com/running-deepseek-r1-locally-with-ollama-and-docker-9b2b7d05607a

```
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama /bin/bash
ollama pull deepseek-r1:1.5b
ollama run deepseek-r1:1.5b
```

hit the api like this

```
curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-r1:1.5b",
  "messages": [{ "role": "user", "content": "Solve: 25 * 25" }],
  "stream": false
}'
```



https://www.datacamp.com/tutorial/deepseek-r1-ollama


# New pre built Deepseek Docker image 

Build the image. 
Note: this will pull ~5GB (1.5GB for Ollama docker image, then 3.5GB for deepseek)
```bash
docker build -f deepseek-r1.dockerfile -t ollama-deepseek:1.0 
```

Run the container

```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama-deepseek ollama-deepseek:1.0
```

Test the end point is accepting requests, and the model is running.

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-r1:1.5b",
  "messages": [{ "role": "user", "content": "What LLM are you, and what version of that LLM model?" }],
  "stream": false
}'
```

Test it can do something basic (multiply 25 by 25).

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-r1:1.5b",
  "messages": [{ "role": "user", "content": "Solve: 25 * 25" }],
  "stream": false
}'
```

When you are done, you can stop the container with 

```bash
docker container stop ollama-deepseek
```

Note that the container is just stopped, which means you can restart it keeping the context.
If you want to remove the container, to reclaim disk, or to re-run a new version with the same container name

``bash
docker container stop ollama-deepseek
```
