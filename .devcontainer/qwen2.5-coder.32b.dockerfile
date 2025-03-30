FROM ollama/ollama:0.6.2

#Note, this 10s sleep will be drowned by the pull 
RUN ollama serve & sleep 5 && ollama pull qwen2.5-coder:32b

COPY ./entrypoint.671b.sh /entrypoint.sh

EXPOSE 11434