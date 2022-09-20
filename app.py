#Package import
import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from astroquery.simbad import Simbad
from astropy.coordinates import EarthLocation, SkyCoord, AltAz
from astropy.time import Time
import astropy.units as u

Simbad.ROW_LIMIT = 1

def get_airmass(sc):
    t = Time.now()
    loc = EarthLocation.of_site('lowell')
    obj_altaz = sc.transform_to(AltAz(obstime=t, location=loc))
    return obj_altaz.alt.value


#initialising app
app = dash.Dash(
    external_stylesheets = [dbc.themes.DARKLY])



#navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("How it works", href="#"),
                dbc.DropdownMenuItem("The statistics", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Explore",
        ),
    ],
    brand="eShel @ Lowell",
    brand_href="#",
    color="dark",
    dark=True,
)

observe_groups = html.Div(
    [
        dbc.InputGroup([
                dbc.Button("Object", color="primary", id='btn-1'), 
                dbc.Button("Bias", color="primary", id='btn-2'),
                dbc.Button("Dark", color="primary", id='btn-3'),
                dbc.Button("Flat", color="primary", id='btn-4'),
                dbc.Button("ThAr", color="primary", id='btn-5')
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Object: "),
                dbc.Input(placeholder="", type='text', id='target'),
                dbc.Button("Resolve", color="info", className="", id='resolve'),
            ],
            className="mb-3",
        ),  
        dbc.InputGroup(
            [
                dbc.InputGroupText("RA: "),
                dbc.Input(placeholder="", type='text', id='ra'),
                dbc.InputGroupText("DEC: "),
                dbc.Input(placeholder="", type='text', id='dec', className='pr-2'), 
                dbc.Button("Slew Telescope", color="warning", className="me-2", disabled=True),
            ],
            className="mb-3",
        ),  
        dbc.InputGroup(
            [
                dbc.InputGroupText("Altitude: "),
                dbc.Input(placeholder="", type='text', id='airmass', disabled=True),
                dbc.InputGroupText("Object visible: "),
                dbc.Input(placeholder="", type='text', id='obj_visible', disabled=True),
            ],
            className="mb-3",
        ),          
        dbc.InputGroup(
            [
                
                
            ],
            className="mb-3",
        ),  
        dbc.InputGroup(
            [
                dbc.InputGroupText("Number of exposures: "),
                dbc.Input(placeholder="1", type='number', min=1, max=100, step=1),
                dbc.InputGroupText("Exposure time: "),
                dbc.Input(placeholder=30, type='number', min=0, max=1200, step=15),                
            ],
            className="mb-3",
        ),         
        dbc.Button("Expose", color="success", className="me-2")    
    ]
)


telescope_groups = html.Div(
    [
        dbc.InputGroup([
                dbc.Button("Connect", color="success", id='tel-connect', className='me-2'),
                dbc.Button("Disconnect", color="danger", id='tel-disconnect', className='me-2'),
                dbc.Button("Home", color="warning", id='tel-home', className='me-2'),
                dbc.Button("Park", color="info", id='tel-park', className='me-2'),
            ],
            className="mb-2",
        ),
    ]
)

control = dbc.Card(
    [
        # dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
        dbc.CardBody(
            [
                html.H4("Telescope Control", className="card-title"),
                telescope_groups,            
                html.H4("Observe", className="card-title"),
                observe_groups,

            ]
        ),
    ],className=""
)

eshel_status_keys = ["eShel", "Mirror", "LED Lamp", "ThAr Lamp", "Tungsten Lamp"]
eshel_status =  dbc.ListGroup(
    [dbc.ListGroupItem([html.Span(className='dot good me-2' ), html.Span(x)]) for x in eshel_status_keys]
    )


status = dbc.Card(
    [
        # dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
        dbc.CardBody(
            [

                html.H4("System Status", className="card-title"),
                html.P(
                    "This card will contain all the status information for the Shelyak/PlaneWave",
                    className="card-text",
                ),
                eshel_status,
            ]
        ),
    ],className=""
)

 
logsheet = dbc.Card(
    [
        # dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
        dbc.CardBody(
            [
                html.H4("Logsheet", className="card-title"),
                 
            ]
        ),
    ],className="ml-2, pr-100"
)


modal = html.Div(
    [
        # dbc.Button("Open", id="open-centered"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Error"), close_button=True),
                dbc.ModalBody("Could not resolve target with Simbad"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-centered",
                        className="ms-auto",
                        color='danger',
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False,
        ),
    ]
)



app.layout = html.Div(className = 'document', children=[
    navbar,
    dbc.Row(html.H1(children = "Spectroscopy @ TiMo", className = "text-center p-3", style = {'color': '#EFE9E7'})),
    dbc.Row(html.H3(children = "Control system for the eShel and 0.7-m PlaneWave.", className = "text-center p-2 text-light ")),
    dbc.Row([dbc.Col(control, className='w-50'), dbc.Col(status, className='w-50')],className="pad-row, mt-3", ),
    dbc.Row([dbc.Col(logsheet, className='w-100')], className="pad-row, mt-3", ),
    modal
    ])
# ])

target = ""

@app.callback(Output("modal-centered", "is_open"),
    Output("ra", "value"), Output("dec", "value"),
    Output('airmass', 'value'),
    Output('obj_visible', 'value'),
    [Input("resolve", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
    State("target", "value")
              )
def toggle_modal(n1, n2, is_open, target):
    if (n1 is not None) and (n2 is not None) and (target is not None):
        if n1 > 0:
            qr = Simbad.query_object(target)
            if qr is None:
                return not is_open, "", "", -90, 'False'
            else:
                sc = SkyCoord(qr[0]['RA'], qr[0]['DEC'], unit=(u.hourangle, u.deg))
                ra = sc.ra.to_string(unit=u.hourangle, sep=':', pad=True, precision=2)
                dec = sc.dec.to_string(unit=u.deg, sep=':', pad=True, precision=2, alwayssign=True)
                obj_alt = get_airmass(sc)
                print(obj_alt)
                if (obj_alt > 15) :
                    obj_vis_bool = 'True'
                else:
                    obj_vis_bool = 'False'
                return is_open, ra, dec, f"{obj_alt:.2f}", obj_vis_bool
    else:
        return False, "","", 90,'True'


@app.callback(
    [[Output(f"btn-{i}", "className") for i in range(1, 6)],
        Output("target", "disabled")],
        Output("target", "value"),
    [Input(f"btn-{i}", "n_clicks") for i in range(1, 6)],
)
def set_active(*args):
    button_ids = {"btn-1":{"object":"", "mirror":1, "flat_lamp":0, "thar_lamp":0},
    "btn-2":{"object":"Bias", "mirror":1, "flat_lamp":0, "thar_lamp":0},
    "btn-3":{"object":"Dark", "mirror":1, "flat_lamp":0, "thar_lamp":0},
    "btn-4":{"object":"Flat", "mirror":1, "flat_lamp":1, "thar_lamp":0},
    "btn-5":{"object":"ThAr", "mirror":1, "flat_lamp":0, "thar_lamp":1},
    }
    ctx = dash.callback_context
    if not ctx.triggered or not any(args):
        return  ['me-2 active'] + ["me-2" for _ in range(2, 6)], False,""
    # get id of triggering button
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    #1 = object, 2=bias, 3=dark, 4=flat, 5=thar
    print(button_id)
    if button_id == "btn-1":
        obj_enabled = False
    else:
        obj_enabled = True
    return ["me-2 active" if button_id == f"btn-{i}" else "me-2" for i in range(1, 6)], obj_enabled, button_ids[button_id]['object']

if __name__ == '__main__':
    app.run_server(debug=True)