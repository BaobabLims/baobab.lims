# Set nginx base image
FROM nginx

# Author / Maintainer
MAINTAINER Thoba Lose 'thoba@sanbi.ac.za'

RUN rm /etc/nginx/nginx.conf

# Copy custom configuration file from the current directory
COPY nginx.conf /etc/nginx/nginx.conf
