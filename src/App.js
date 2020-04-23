import React from "react";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";
import Button from "react-bootstrap/Button";

import { BrowserRouter as Router, Route, Redirect } from "react-router-dom";

export default function App() {
  return (
    <Router>
      <Route exact path="/" component={Home} />
      <Route exact path="/game/:gameName" component={Game} />
    </Router>
  );
}

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.gameNameInput = React.createRef();
    this.state = {};
  }

  onCreateGame = () => {
    const response = fetch("/game", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ game_name: this.gameNameInput.current.value }),
    }).then(response => response.json()).then(data => 
      this.setState({
        shouldRedirect: true,
        name: data.name,
      }))
  };

  render() {
    const contents = (
      <div>
        {this.state.shouldRedirect && (
          <Redirect to={`/game/${this.state.name}`} />
        )}
        <h1>Taboo</h1>
        <div>
          Play Taboo online across multiple devices on a shared board. To create
          a new game or join an existing game, enter a game identifier and click
          'GO'.{" "}
          <InputGroup className="mb-3">
            <FormControl
              placeholder="Name of game"
              aria-label="Name of game"
              ref={this.gameNameInput}
            />
            <InputGroup.Append>
              <Button onClick={this.onCreateGame}>Go</Button>
            </InputGroup.Append>
          </InputGroup>
        </div>
      </div>
    );
    return contents;
  }
}

class Game extends React.Component {
  constructor(props) {
    super(props);
    this.gameName = props.match.params.gameName;
  }

  render() {
    return <h1>{this.gameName}</h1>;
  }
}
