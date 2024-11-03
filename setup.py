from setuptools import setup, find_packages
def parse_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()
setup(
    name='emNaviBase',  
    version='0.1.0',         
    author='hyaline',      
    author_email='hyaline@emnavi.tech', 
    description='emNaviBase backend',  
    packages=find_packages(),  
    classifiers=[  
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', 
    install_requires=parse_requirements('requirements.txt'),

)
