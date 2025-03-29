FROM ollama/ollama:0.6.2

#Can I just do this? Note, this 10s sleep will be drowned by the pull
#RUN ollama serve & sleep 5 && ollama pull gemma:2b

RUN ollama serve & sleep 5 && ollama pull deepseek-r1:1.5b

# RUN ollama pull deepseek-r1:1.5b

# RUN ollama run deepseek-r1:1.5b

# COPY ./ollama/pull_model.sh /pull_model.sh

# RUN chmod +x /pull_model.sh

# RUN /pull_model.sh


EXPOSE 11434