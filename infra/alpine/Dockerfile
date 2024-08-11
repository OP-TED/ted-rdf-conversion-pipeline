# Use the official Alpine Linux image
FROM alpine:3.20

# Update the package list and install sudo and shadow (which includes useradd)
RUN apk --no-cache add sudo=1.9.15_p5-r0 shadow=4.15.1-r0

# Create a new non-root user and set a home directory
RUN useradd -m newuser

RUN echo "newuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Switch to the non-root user
USER newuser

# Set the working directory to the new user's home directory
WORKDIR /home/newuser
COPY libraries .
# Default command to execute when running the container
CMD ["/bin/sh"]