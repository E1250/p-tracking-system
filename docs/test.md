Now i am in the last step, it had not be the last step but no worries.

first going to start with ruff, it is a combine between more than one tool, it is a linter, and also formatter, and it is fast. It force developer to write good style code.

Feel free to add the rules that you want ruff to apply and then run `ruff format .` to format the code based on the vars you added

now for linting, fixing the code `ruff check .` for checking and `ruff check --fix .` for fixing. if the fixing didn't fix all stuff, then it means you have to manually fix them. you can run check again after `fix`


Then we come to `pyright`, it is like pydantic testing, check the function types and what you are passing to this function, trying at most as we can to avoid issues from happening 


now regarding `mkdocs`, it is really a great tool to create a dict of tools you have, for an engineer who starts his project, he type `mkdocs new .` and it auto create the .yml file and index.md file. then `mkdocs serve` run a server to show the doc you have.  

now one of the most important things, and i see it is fixing a real issue i faced before, which is commiting then founding import errors and so on, letting me just fix and try to commit again, i remember i have to commit about 15 times fixing really simple issues. `.pre-commit-config.yaml` fixes this, by running tests before commiting

then run this `pre-commit install`, it is one per project, now it is being attached into your .git file. note also that it only test the files in commit

`pre-commit sample-config > .pre-commit-config.yaml` 


also after modifying .pre-commit file , `pre-commit run --all-files`

make sure you run `pre-commit install` after modifying .pre-commit file, otherwise it will not work.