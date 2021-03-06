import setuptools
import tarfile
import os

pkg_name = "conversationkg"



def setup_sample_data():
    data_dir = os.path.join(pkg_name, "sample_data")
        
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)        
        for mailing_ls_file in filter(lambda f: f.endswith(".tar.gz"), 
                                      os.listdir("email_data_compressed")):
            tar = tarfile.open(os.path.join("email_data_compressed", mailing_ls_file), "r:gz")
            tar.extractall(data_dir)
            tar.close()
            
        with open(os.path.join("email_data_compressed", "load.py")) as reader:
            with open(os.path.join(data_dir, "load.py"), "w") as writer:
                writer.write(reader.read())
    else:
        if os.listdir() == []:
            raise Exception("we're here: " + os.path.abspath(os.getcwd()) +\
                            "\ncontents of conversationkg/sample_data: " + os.listdir(data_dir))


def read_requirements():
    with open("requirements.txt") as handle:
        reqs = [r.strip() for r in handle if r.strip() and not r.startswith("#")]
        return reqs


def get_desctription():
    with open("README.md") as handle:
        return handle.read()



######


setup_sample_data()


setuptools.setup(
    name="conversationkg",
    version="0.0.1",
    author="Valentin Vogelmann, Paul Groth",
    author_email="p.groth@uva.nl",
    description="A framework for extracting knowledge graphs" 
                "based on conversational structure from email archives.",
    long_description=get_desctription(),
    long_description_content_type="text/markdown",
    url="https://github.com/INDElab/conversationkg",
    packages=["conversationkg",
              "conversationkg.kgs", 
              "conversationkg.conversations",
              "conversationkg.sample_data"],  # setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    install_requires=read_requirements(),
    package_data={"conversationkg": ["sample_data/*/*.json"]}, # sample_data/ietf-http-wg/all.json"]}
    include_package_data=True
)
