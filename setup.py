import setuptools
import tarfile
import os

pkg_name = "conversationkg"


data_dir = os.path.join(pkg_name, "sample_data")

if not os.path.isdir(data_dir):
    os.mkdir(data_dir)
    
    
#    
#    raise Exception(os.getcwd(), os.listdir("."),
#            list(filter(lambda f: f.endswith(".tar.gz"), os.listdir("email_data_compressed"))))
    
    
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


with open("README.md") as handle:
    full_description = handle.read()


    
#raise Exception(os.path.exists("conversationkg/sample_data/ietf-http-wg/all.json"))
#raise Exception(os.getcwd(), os.listdir("."), os.listdir("conversationkg/sample_data"))

setuptools.setup(
    name="conversationkg",
    version="0.0.1",
    author="Valentin Vogelmann",
    author_email="v.l.vogelmann@uva.nl",
    description="A framework for extracting knowledge graphs" 
                "based on conversational structure from email archives.",
    long_description=full_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pgroth/conversationkg",
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
    package_data={"conversationkg": ["sample_data/*/*.json"]}, # sample_data/ietf-http-wg/all.json"]}
    include_package_data=True
)
