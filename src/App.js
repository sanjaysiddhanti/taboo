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

function getFetchUrl(path) {
  return process.env.REACT_APP_SERVER_URL === undefined ? path : `${process.env.REACT_APP_SERVER_URL}${path}`
}

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.gameNameInput = React.createRef();
    this.state = {
      errorMsg: "",
    };
  }

  onCreateGame = () => {
    const response = fetch(getFetchUrl("/game"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ game_name: this.gameNameInput.current.value }),
    })
      .then((response) => {
        if (!response.ok) {
          // response.json().then((data) => {
          //   throw Error(data.message);
          // });
          throw response;
        }
        return response.json();
      })
      .then((data) =>
        this.setState({
          shouldRedirect: true,
          name: data.name,
        })
      )
      .catch((response) => {
        const errorMsg = response.json().then((data) => {
          console.log(data);
          this.setState((state, _) => ({
            errorMsg: state.errorMsg.concat(data.message),
          }));
        });
      });
  };

  renderErrorMsg = () => <h3>Error creating game: {this.state.errorMsg}</h3>;

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
        {this.state.errorMsg && this.renderErrorMsg()}
      </div>
    );
    return contents;
  }
}

class Game extends React.Component {
  constructor(props) {
    super(props);
    this.gameName = props.match.params.gameName;
    this.state = { errorMsg: "" };
  }

  componentDidMount() {
    this.fetchPrompts(1);
  }

  fetchPrompts = (page) => {
    const response = fetch(getFetchUrl(`/game/${this.gameName}/prompts?page=${page}`), {
      method: "GET",
    })
      .then((response) => {
        if (!response.ok) {
          throw response;
        }
        return response.json();
      })
      .then((data) =>
        this.setState({
          prompts: data.prompts,
          page: data.page,
          numPages: data.num_pages,
          currentPromptIndex: 0,
        })
      )
      .catch((response) => {
        const errorMsg = response.json().then((data) => {
          this.setState((state, _) => ({
            errorMsg: state.errorMsg.concat(data.message),
          }));
        });
      });
  };

  renderErrorMsg = () => <h3>Error loading game: {this.state.errorMsg}</h3>;

  morePromptsExist = () =>
    this.state.currentPromptIndex < this.state.prompts.length - 1 ||
    this.state.page < this.state.numPages;

  nextPrompt = () => {
    const response = fetch(getFetchUrl("/game_prompt/update"), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        game_prompt_id: this.state.prompts[this.state.currentPromptIndex].id,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw response;
        }
        return;
      })
      .then(this.fetchPrompts(1))
      .catch((response) => {
        const errorMsg = response.json().then((data) => {
          console.log(data);
          this.setState((state, _) => ({
            errorMsg: state.errorMsg.concat(data.message),
          }));
        });
      });
  };

  render() {
    if (this.state.prompts) {
      const currentPrompt = this.state.prompts[this.state.currentPromptIndex];
      const listItems = currentPrompt.banned_words.map((word) => (
        <li key={word}>{word}</li>
      ));

      return (
        <div className="col">
          <h1>{this.gameName}</h1>
          <div classsName="card">
            <h3 className="clue">{currentPrompt.target_word}</h3>
            <ul className="taboo-words">{listItems}</ul>
          </div>
          {this.morePromptsExist() && (
            <Button variant="success" onClick={this.nextPrompt}>
              Next Prompt
            </Button>
          )}
          {this.state.errorMsg && this.renderErrorMsg()}
        </div>
      );
    }
    return null;
  }
}
