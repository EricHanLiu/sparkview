from bloom.celery import app


@app.task(bind=True)
def global_healthcheck(self):
    """
    Runs all healthchecks
    :param self:
    :return:
    """
    pass
