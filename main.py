import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from oidc import OIDCService
from starlette.middleware.sessions import SessionMiddleware

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

jinja_env = Environment(loader=FileSystemLoader("templates"))

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret")

oidc_service = OIDCService()


@app.get("/google-oidc/")
async def root(request: Request):
    try:
        home_temp = jinja_env.get_template("homepage.html")
        html_content = home_temp.render()
        return HTMLResponse(content=html_content)
    except TemplateNotFound as e:
        return HTTPException(status_code=404, detail=f"Template not found: {e}")


@app.get("/google-oidc/login")
async def login(request: Request):
    authorization_url, state = oidc_service.get_auth_server_url()
    print("*GOOGLE AUTH SERVER URL* (Step 2)")
    print(authorization_url)
    print()
    request.session["state"] = state
    return RedirectResponse(authorization_url)


@app.get("/google-oidc/auth")
async def auth(request: Request):
    state = request.session.get("state")
    if not state:
        raise HTTPException(status_code=400, detail="State not found in session")
    authorization_response = str(request.url)
    print("*RESPONSE CODE* (Step 7)")
    print(authorization_response)
    print()

    try:
        token_info, access_token, userinfo = oidc_service.authorize(authorization_response)
        print("*TOKEN INFO* (Step 9)")
        print(token_info)
        print()

        print("*USERINFO* (Step 13)")
        print(userinfo)
        print()
        request.session["access_token"] = access_token
        userinfo = userinfo
        template = jinja_env.get_template("profile.html")
        html_content = template.render(userinfo=userinfo)
        return HTMLResponse(content=html_content)
    except ValueError as e:
        return HTMLResponse(content=f"Error: Invalid token: {e}", status_code=400)
