import axios from "axios";
import * as settings from '../util/settings';


export default axios.create({
  baseURL: settings.API_SERVER + '/api/',
  headers: {
    "Content-type": "application/json"
  }
});