FROM node:16

WORKDIR /app

COPY frontend/package*.json ./

RUN npm install

COPY frontend/ .

# Update API URL to point to the backend container - with error handling
RUN FILES=$(grep -r "localhost:8000" --include="*.js" . | cut -d: -f1 || echo "") && \
    if [ -n "$FILES" ]; then \
        sed -i 's|http://localhost:8000|http://backend:8000|g' $FILES; \
    else \
        echo "No files with localhost:8000 found. Skipping replacement."; \
    fi

EXPOSE 3000

CMD ["npm", "start"]