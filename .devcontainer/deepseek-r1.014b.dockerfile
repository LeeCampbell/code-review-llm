FROM ollama/ollama:0.6.2

#Note, this 10s sleep will be drowned by the pull 
RUN ollama serve & sleep 5 && ollama pull deepseek-r1:14b

COPY ./entrypoint.014b.sh /entrypoint.sh

EXPOSE 11434