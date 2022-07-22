FROM alpine:latest

# Add crontab file in the cron directory
ADD docker/cleanup/crontab /home/cleanup-crontab

# Give execution rights on the cron job
RUN chmod a+x /home/cleanup-crontab

# add the cron
RUN crontab /home/cleanup-crontab

ENTRYPOINT ["/usr/sbin/crond", "-f"]