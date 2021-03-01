# coding=utf-8

from __future__ import absolute_import

import os.path
import logging

from talos.core import config
from talos.core.i18n import _

CONF = config.CONF
LOG = logging.getLogger(__name__)


class Apispec(object):
    name = "openapi.apispec"

    def on_get(self, req, resp, **kwargs):
        filepath = CONF.openapi.filepath
        filesize = os.path.getsize(filepath)
        stream = open(filepath, 'rb')
        resp.set_stream(stream, filesize)
        resp.set_header('Content-Type', 'application/octet-stream')


class Redoc(object):
    name = "openapi.redoc"

    def on_get(self, req, resp, **kwargs):
        html = '''<!DOCTYPE html>
<html>
  <head>
    <title>ReDoc</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url='/terminal/apispec'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
'''
        resp.body = html
        resp.set_header('Content-Type', 'text/html')


class Swagger(object):
    name = "openapi.swagger"

    def on_get(self, req, resp, **kwargs):
        html = '''<!-- HTML for static distribution bundle build -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Swagger</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css" />
  </head>

  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js" charset="UTF-8"> </script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-standalone-preset.js" charset="UTF-8"> </script>
    <script>
    window.onload = function() {
      
      // Begin Swagger UI call region
      const ui = SwaggerUIBundle({
        "dom_id": "#swagger-ui",
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout",
        validatorUrl: "https://validator.swagger.io/validator",
        url: "/terminal/apispec",
      })
      
      
      // End Swagger UI call region


      window.ui = ui;
    };
  </script>
  </body>
</html>
'''
        resp.body = html
        resp.set_header('Content-Type', 'text/html')