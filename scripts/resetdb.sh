#!/bin/sh
psql -h localhost -U postgres -c "DROP DATABASE generator"
psql -h localhost -U postgres -c "CREATE DATABASE generator"
