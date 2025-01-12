# Etap 1: Budowanie aplikacji
FROM node:18-bullseye as build

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików package.json i package-lock.json
COPY package.json package-lock.json ./

# Instalacja zależności
RUN npm install --legacy-peer-deps


# Kopiowanie reszty aplikacji
COPY . ./

# Budowanie aplikacji
RUN npm run build

# Etap 2: Serwowanie aplikacji za pomocą Nginx
FROM nginx:stable

# Usunięcie domyślnej konfiguracji Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Kopiowanie własnej konfiguracji Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Kopiowanie zbudowanej aplikacji do katalogu serwowanego przez Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Otwarcie portu 80
EXPOSE 3000

# Uruchamianie Nginx
CMD ["nginx", "-g", "daemon off;"]
