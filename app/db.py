"""
Functions for connecting to Neo4j database
Adapted from https://github.com/neo4j-graphacademy/app-python/blob/main/api/neo4j.py
"""

from flask import Flask, current_app

from neo4j import GraphDatabase


def init_driver(uri, username, password):
    """Initialize db driver"""
    current_app.driver = GraphDatabase.driver(uri, auth=(username, password))
    current_app.driver.verify_connectivity()
    return current_app.driver


def get_driver():
    """Get the instance of the Neo4j driver"""
    return current_app.driver


def close_driver():
    """Close db driver and all sessions"""
    if current_app.driver != None:
        current_app.driver.close()
        current_app.driver = None

        return current_app.driver
