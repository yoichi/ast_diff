import setuptools

setuptools.setup(
    name='ast_diff',
    url='https://github.com/yoichi/ast_diff',
    author='Yoichi Nakayama',
    author_email='yoichi.nakayama@gmail.com',
    packages=setuptools.find_packages(),
    setup_requires=[
        'flake8',
    ],
    test_suite='test_ast_diff'
)
