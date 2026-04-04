## Multi tracking systems
* https://github.com/mikel-brostrom/boxmot
* https://developer.nvidia.com/deepstream-sdk

* https://www.cvat.ai/resources/blog/top-ai-models-video-tracking

The ides for now, We have created some AI models, and we can use it in two ways
* for 2d camera status-
    * Detect fire or any danger in the place
    * Draw the human in the 2d dashboard. (Detection and Depth)

* For 2d map
    * Car accedents or crows to close the road
    * Path finding with shortest path. 

Keep it simple mate, 
* Detectoins, only People, fire and Accident or crowd. 
* Show red camera when all of these being detected, but people, show real place. 
* For map, Close the road, and path finding, Publish the project after the 2d dashboard, then work on the 2d map. 

Make sure you hanlde memory correctly, like to emptry torch cache when required, check it further later, `torch.cuda.empty_cache()`

https://colab.research.google.com/drive/1WIXVjOfResUDBX9HfXn7fMSxIWogRaqL?usp=sharing


The model profiler link - https://app.clear.ml/projects/bffe65b5fe1649dd9d202e181ba92fe0/experiments/f57871573c9d4d969dd5867004857d99/output/execution


so the best practise for this, you upload your models on HF, Each model must have its own HF repo model, and its info, but you can add more than one version of the same model under the same repo. ex. YOLOs, YOLOm, YOLOl at one repo. and mention the version in the pull to fetch the correct one. 

Also i faced a new kind of issue today, it is regarding the sub-repo depth, i noticed on Github he is not actually reading it at all. As it has its own git. 
using this, i could remove a specific file from cache `git rm --cached ai/depth/depth_anything_v2`

and this to get back to the last commit, git reset --soft HEAD~1

This line also is really important and great, 
`git commit --amend --no-edit`
it add the current modification to the existing commit, like you fixed a typo, it doesn't need a full commit again. 
If you already pushed, do this again, and the force push. 
also try to use this, `git rebase -i HEAD~2`, it is really useful. 