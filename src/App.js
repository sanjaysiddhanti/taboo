import React from "react";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";
import Button from "react-bootstrap/Button";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.gameNameInput = React.createRef();
  }

  onCreateGame = () => {
    const response = fetch("/game", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ game_name: this.gameNameInput.current.value }),
    }).then((response) => response.json());
    return response;
  };

  render() {
    const contents = (
      <div>
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

export default App;
