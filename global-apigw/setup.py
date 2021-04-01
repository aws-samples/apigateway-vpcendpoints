import setuptools

CDK_VERSION = "1.101.0"

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="global_apigw",
    version="0.0.1",
    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "global_apigw"},
    packages=setuptools.find_packages(where="global_apigw"),
    install_requires=[
        f"aws-cdk.core=={CDK_VERSION}",
        f"aws-cdk.aws-apigatewayv2=={CDK_VERSION}",
        f"aws-cdk.aws-apigatewayv2-integrations=={CDK_VERSION}",
        f"aws-cdk.aws-elasticloadbalancingv2-targets=={CDK_VERSION}",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
