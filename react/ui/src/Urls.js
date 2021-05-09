import React from "react";
import { BrowserRouter, HashRouter, Route, Switch, Redirect } from "react-router-dom";

import Home from "./screens/Home";
import Index from "./index";

function Urls(props) {

    return (
        <div className='Home'>
            <HashRouter basename="./">
                <Switch>
                    <Route exact path="/*"> <Home {...props} /></Route>
                </Switch>
            </HashRouter>
        </div>
    )
};

export default Urls;