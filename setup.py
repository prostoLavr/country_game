from setuptools import setup, find_packages


install_requires = [
    'pygame',
    'pillow'
]

setup(
    name='country_game',
    version="0.0.1",
    description='Country Game',
    platforms=['POSIX'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'run_game=country_game.main:main'
        ]
    }
)

