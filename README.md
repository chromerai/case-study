# Important:

- The `backend` folder contains the following directories: 
    - agents - The crux of the Agentic Architecture:<br>
        Currently, 4 agents:<br>
            1.  Central Agent: Main agent responsible for communication between the user and other agents. It primarily gathers information from the user inputs and extracts them for the Tool Manager. It also requests for more, if it feels the information to be insufficient.<br>
            2.  Tool Manager: Primarily, responsible for figuring out the appropriate tool to be used based on the user's query. Provides back the tool outputs to the response generation agent for appropriate response generation<br>
            3.  Response Generation: Generates responses based on the tool output and conversation history.<br>
            4.  Judge Agent: Checks the generated response by the response generation agent and evaluates and decides whether to APPROVE/DISAPPROVE sends feedback to the central agent in the latter case so that agent can again interact with the user to get essential inputs.
            If response is APPROVED, the workflow then comes to the end and user sees the response from the ai assistant.
            <br>
    - config - To load the environment variables
    - database -  Neo4j, the folder also containa a scrape.ipynb notebook, that contains the code for scraping as well as adding it to the database.
    - tools - Currently there are only four types of tools, Information rertrieval, Recommendation, Compatibilty Checker(part and model), Symptom Analysis Tool  
    - utils -  currently only calls for the `OPENAI` Client, but it can be extended to include Many LLMs.



## The Single most import aspect of the entire Architecture:

```
class State(TypedDict):
    user_input: Annotated[List[str], "mutable"]
    conversation_history: Annotated[List[str], "mutable"]
    extracted_info: Dict[str, Any]
    tool_output: Dict[str, Any]
    next_step: Annotated[List[str], "mutable"]
    tool_explanation: Annotated[List[str], "mutable"]
    generated_response: Annotated[List[str], "mutable"]
    feedback: str
```

# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
