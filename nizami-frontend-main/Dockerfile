# Build stage
FROM node:20-alpine AS build

# Accept build configuration as argument (default to production)
ARG CONFIGURATION=production

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy project files
COPY . .

# Build the Angular app with the specified configuration
RUN npm run build -- --configuration ${CONFIGURATION}

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/dist/nizami-frontend/browser /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

