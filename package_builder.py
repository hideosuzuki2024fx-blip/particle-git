import shutil, os, textwrap, pathlib

base = pathlib.Path(".")
pkg = base / "ai_core_gpt"
pkg.mkdir(exist_ok=True)

# 主要モジュールをコピー
shutil.copy("particle_exporter.py", pkg / "exporter.py")
shutil.copy("gpt_design.py", pkg / "design.py")
shutil.copy("gpt_runtime.py", pkg / "runtime.py")
for sub in ["integration_pipeline/pipeline_controller.py", "integration_pipeline/optimizer.py"]:
    target = pkg / os.path.basename(sub)
    shutil.copy(sub, target)

# __init__.py
(pkg / "__init__.py").write_text("__all__ = ['exporter','controller','optimizer','design','runtime']\n", encoding="utf-8")

# setup.py
(base / "setup.py").write_text(textwrap.dedent('''\
from setuptools import setup, find_packages
setup(
    name="ai_core_gpt",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    description="Hallucination-Resistant GPT Reliability Framework",
    author="MaoGon",
)
'''), encoding="utf-8")

# README.md
(base / "README.md").write_text("# AI Core GPT\nHallucination-resistant GPT reliability framework.", encoding="utf-8")

# requirements.txt
(base / "requirements.txt").write_text("json\nlogging\npathlib\nuuid\nre\n", encoding="utf-8")

print("[package] ai_core_gpt package structure generated successfully.")
