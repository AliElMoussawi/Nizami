# Stage 1: Build Angular app
FROM node:20-alpine AS build

# Accept build configuration as argument (defaults to production)
ARG CONFIGURATION=production

WORKDIR /app

# Copy dependency files and install (cached separately)
COPY package*.json ./
RUN npm ci

# Copy project source
COPY . .

# Clear Angular cache before building (optional - remove if not needed)
RUN rm -rf .angular/cache || true

# Build Angular app for the given configuration
RUN npm run build -- --configuration ${CONFIGURATION}

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy build output (adjust folder name if no "browser" subfolder exists)
COPY --from=build /app/dist/nizami-frontend/browser /usr/share/nginx/html
# Custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
