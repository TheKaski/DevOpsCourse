FROM nginx:stable-alpine
RUN apk add --no-cache apache2-utils
# Create the .htpasswd file with a default username and password
# This would NEVER be used in production but I wanted an easy way to TEST the
# application without the need to create password on linux machine when developping with windows
# that I figured that I could just use the container to generate its own default password when started
# so that the file  will always be there when needed
RUN htpasswd -bc /etc/nginx/.htpasswd admin secret

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]