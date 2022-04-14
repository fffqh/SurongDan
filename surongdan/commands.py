from surongdan import app, db
import click 


# Flask 命令
@app.cli.command()
def initdb():
    db.create_all()
    click.echo("Initialized database.")

@app.cli.command()
def dropdb():
    db.drop_all()
    click.echo("Droped database.")


