import React, { Component } from 'react';
import {render} from 'react-dom';
import HomePage from './HomePage'
import RoomJoinPage from './RoomJoinPage';
import CreateRoomPage from './CreateRoomPage';

/* start react app => $npm run dev */

export default class App extends Component { 
    constructor(props) {
        super(props);
        this.state = {
            name : "Test Website"
        }
    }

    render() {
        return (
            <div className="center">
                <HomePage />
            </div>
        )
    }
}

const appDiv = document.getElementById("app");
render(<App />, appDiv);

// render(<App name="berkay"/>, appDiv); 