let API_SERVER_VAL = '';

switch(!process.env.NODE_ENV) {
    case 'production':
        API_SERVER_VAL = process.env.REACT_APP_API_SERVER;
    case 'development':
        API_SERVER_VAL = 'http://localhost:8100';
        break;
    default:
        API_SERVER_VAL = 'http://localhost:8100';
        break;
}

export const API_SERVER = API_SERVER_VAL;