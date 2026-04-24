


TODO
- [] Make sure in AI you have.
    * Detection (Person, Fire or a danger, Accident, Crowd)
    * Depth
- [] Backend
    * Take image, apply ai, Save them for broadcasting. 
    * Sending these to dashboards
- [] Dashboard
    * 2D Canvas -> Camera status in case of danger
                -> Person Location using depth
    * 2D Map    -> Camera status in case of danger or crowd.
                -> Path finding.

Do these and publish on HF. The goal of this project is to get advices to check the End to end Projects. Clean Code and Arch, Project management. Real-Time. 

A product-grade AI surveillance system that automatically detects incidents from live camera streams and sends real-time alerts for small to medium offices.

# Recommended build sequence (iterative, test-driven)

* Project skeleton + config loader + path discovery + device utils.
* Isolated model classes (detector, depth_est) + simple inference scripts/tests.
* Pipeline class with process_frame + basic association.
* Structured output schema + minimal visualization utils.
* Adapter: simple video script + dashboard skeleton (e.g., Streamlit loop loading pipeline once).
* Profiling, tuning (tracker params, input resize, half-precision), tests.
* Polish: logging, error handling per-frame, config-driven model selection.


### The Plan

I searched for most useful tools and packages that i might use to help me keep best practices for clean code and architecture. 


The plan for now, is that i am going to use the backend to handle all the processing uisng parallel, as this way it better and professional in my case. also to avoide the required part of edge compuations. 


also i got another plan, it is about the trade off between batch images or single image processing. 
What GPT thiks, single frame is prefered for the real time detection, and batched for analysis. i think of the balance. Small batch. i just read the rest, ai also suggessted the same. hahahah. mostly from 2 to 5 frame per batch. 

## Preparing the env
### Conda env
i faced an issue today, it was about conda when i tried to pip unintall a package i have, it broke the whole conda i have.
* Never touch the base conda, create local envs.
* Use Conda as much as you can
* Export your conda env as .yml
* If required, use pip after conda installation, and never uninstall using pip, recreate the env.
* Always keep the base env empty and safe and create an env for each project you have. 
to install `ultralytics` with `torch` cuda using conda i used this comand
`conda install -c pytorch -c nvidia -c conda-forge pytorch torchvision pytorch-cuda ultralytics`

After a while, i really faced tons of problems like not ability to select the conda env from the vs terminal, so it is really advised to always use --name while creating the conda env.

what i am going to do rn, is to rename my env.

you have two ways:
1. Create is locally in your project dir, then add it to the config to be found.
```cmd
conda config --append envs_dirs /path/to/projects_folder
```
2. Rename it to be added in the config directly (Note that you can't both --prefix and --name together.)
```cmd
conda rename -p /absolute/path/to/your/env_folder new_name
```

3. Clone it with the new name. 
```cmd
conda create --name new_name --clone /path/to/your/env_folder
```


### Can't modify the env from terminal. 
I faced another issue rn, the ide terminal wasn't changing conda env at all, after some research, it is only being resolved by
```cmd
conda init powershell
conda init bash
```
then restart

--- 

## Pydantic and Data Validation
Most popular data validation library, alternative and best practive instead of using `isinstace` to check for the value type.

Pydantic solves all these problems by combiing three powerful concepts: Type hint, runtime valudation, automatic serialization. 

> Deal with pydantic as a contract, validating data to be able to send it to another layer and get the expected results. 

Resources
* https://www.datacamp.com/tutorial/pydantic
* https://www.geeksforgeeks.org/python/introduction-to-python-pydantic-library/
* https://medium.com/@marcnealer/a-practical-guide-to-using-pydantic-8aafa7feebf6


```
conda search pydantic # to search if exists
conda install -c conda-forge pydantic
```

## Configuration
> Core mental model: "Configuration is documentation + contract + safety net"

Think of your config file(s) as:
* The single source of truth about "how this system behaves right now"
* Executable documentation — anyone (you in 3 months, a new teammate) should understand almost everything important just by reading the YAML
* A guardrail — wrong values should crash early (at startup) with a clear message, not fail mysteriously at 2 a.m.
* A negotiation point between components — instead of hard-coupling everything, components ask "what did the human decide?" via the config object


the most important thing in my opinion is the config file, which reads the constants like the path of the models to make sure it is always being modified from one place, and again pydantic is going to be really helpful in this part also, as it offers validation on the inputs of values in yaml which what users edit.

How it works, The use modify the YAML file, python takes these values, validate using pydantic and then return so it can be used again.
* https://docs.pydantic.dev/latest/concepts/pydantic_settings/

Regaring config files like config.yaml and .env
.env  -> for secrets and 
.env.example -> temp for others
config.yaml -> Shared defaults
configs   -> Folder to manage other yaml files.
> Overall, Yaml contains the defualts, override using env for your system if needed. 


# Put here in device related settings, Secretes, paths in the local machine, everything you don't want to share outside
# Put real values here, Local Overrides and machine-specific settings
# Put overrides here


* https://www.datacamp.com/blog/what-is-yaml

Summary Table

Tool / PackageFree?Open Source?NotesstructlogYesYespip installpsutilYesYespip installprometheus-clientYesYespip installpyinstrumentYesYespip installmemory-profilerYesYespip installFastAPI + uvicornYesYespip installlocustYesYespip installjqYesYesSingle binary or package managerPrometheusYesYesSelf-hostedGrafana (OSS version)YesYesSelf-hosted (cloud version has paid tiers)Grafana LokiYesYesSelf-hosted


docker run --gpus all --shm-size=2g -it --name test nvcr.io/nvidia/pytorch:26.01-py3


> Please always use `pip` to install required packages, and export yml file, as when i tried to always use `conda-forge` sometimes packages are not updated and cause the whole env to broke directly. 

https://opacus.ai/


Now when i tried to check more before importing packages on other folders, or in other working start embedding functions, i faced some import issues. i wanted to test functions before embedding, After some search, the best for this here is installing as a package, a local package, and pyproject.toml is best for this. but you should create one for each group of functions (ai folder for example) as not the full project should be packaged. 
after creating the `pyproject.toml` file, and create `__init__.py` file, now you can install it using `pip install -e ./ai`
Dont forget to download first `hatchling` 

if you wanted to unintall the package again, you still can use `pip uninstall package_name`

after really suffering here to be able to access a module from another folder, and trying really different ways, finally it worked after adding this to vscode settings. 
```
"terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}"
    }
```


todays also i learned some great thing, something called Git subtree, which i use to send only a sub folder from this git to my hugging face git to store and deploy the backend, 
you add the url like this - `git remote add space https://huggingface.co/spaces/e1250/your-space-name`
and then push like this - `git subtree push --prefix=backend space main`
