import setuptools


with open("README.md") as handle:
    full_description = handle.read()



# EXTRACT DATA FROM EMAIL_DATA
# MOVE TO RIGHT PLACES
# USE package_data={"" : [*.json]}, include_package_data=True ?
# ADD MANIFEST.in TO INCLUDE THAT DATA ?
    
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
              "conversationkg.conversations"],  # setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    package_data={"" : ["conversationkg/email_data/ietf-http-wg/all.json",
                        "conversationkg/email_data/public-credentials/all.json"]},
    include_package_data=True
)
