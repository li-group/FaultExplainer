import io from "socket.io-client";
import configData from './config.json';

export const socket = io(`${configData.SERVER_URL}`);
