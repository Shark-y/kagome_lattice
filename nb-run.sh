#
# Remote server: https://docs.anaconda.com/anaconda/user-guide/tasks/remote-jupyter-notebook/
# https://stackoverflow.com/questions/35545402/how-to-run-an-ipynb-jupyter-notebook-from-terminal
# run a notebook and produce a new notebook: jupyter nbconvert --execute --to notebook <notebook>
# replace the existing notebook: jupyter nbconvert --execute --to notebook --inplace <notebook>

jupyter nbconvert --execute --ExecutePreprocessor.timeout=-1 --to notebook solution.ipynb &
