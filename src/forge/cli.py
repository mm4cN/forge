import typer

from forge.commands.agent import app as agent_app
from forge.commands.settings import register_config_commands
from forge.commands.model import app as model_app
from forge.commands.session import register_session_commands
from forge.commands.tools import register_tool_commands
from forge.commands.usage import register_usage_commands
from forge.commands.review import app as review_app

app = typer.Typer(help="Forge — local coding agent")

app.add_typer(model_app, name="model")

register_config_commands(app)
register_session_commands(app)
register_tool_commands(app)
register_usage_commands(app)
app.add_typer(agent_app)
app.add_typer(review_app)
