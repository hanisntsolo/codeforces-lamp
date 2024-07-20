# Codeforces Lamp

## Overview

The **Codeforces Lamp** project provides a Dockerized solution for integrating with the Codeforces API to track profile ratings and submissions in real-time. This repository contains all the necessary files to build and publish Docker images, making it easy for users to deploy and use the Codeforces Lamp on any platform. Our goal is to streamline the process of accessing and utilizing Codeforces data, offering a ready-to-use, containerized environment for developers and competitive programming enthusiasts.

## What is this project?

- **Set up a real-time smart lamp color based on Codeforces profile rating**:
    Once set up, the system fetches your Codeforces rating and adjusts the lamp color accordingly.
- **Track submissions with real-time smart lamp feedback**:
    The system automatically fetches new submissions and provides the following feedback:
    1. Submissions in process will cause the lamp to flicker, alternating with a breathing orange color.
    2. Accepted submissions will switch the lamp to parrot green before reverting to the rating/profile color after a set delay.
    3. Wrong submissions will turn the lamp red for a certain time before reverting to the rating/profile color after a set delay.

## Prerequisites

- **SMARTLIFE [Android](https://play.google.com/store/apps/details?id=com.tuya.smartlife&hl=en_IN)/[iOS](https://apps.apple.com/in/app/smart-life-smart-living/id1115101477) App**: To add the smart lamp to the Tuya account and get the device's Unique Identifier.
- **Wipro [Smart Lamp/Light Devices](https://amzn.to/3zKYso2)**: Smart light devices connected to the SMARTLIFE App.
- **Tuya Developer Access**: Obtain Tuya developer access to interact with their IoT APIs.
- **Codeforces API Key**: Obtain an API key from Codeforces to interact with the Codeforces system.
- **Set Up Environment Variables in `docker-compose.yml`**:    
    ```yaml
      - CODEFORCES_API_KEY=${CODEFORCES_API_KEY}
      - CODEFORCES_API_SECRET=${CODEFORCES_API_SECRET}
      - TUYA_ACCESS_ID=${TUYA_ACCESS_ID}
      - TUYA_ACCESS_KEY=${TUYA_ACCESS_KEY}
      - TUYA_BULB_ID=${TUYA_BULB_ID}
    ```

## Features

- **Pre-configured Environment**: Includes all dependencies and configurations required to interact with the Codeforces API.
- **Modular Architecture**: Designed with modularity in mind, making it easy to extend and customize.
- **Easy Deployment**: Docker images can be created and run with minimal setup.
- **Open Source**: Freely available for anyone to use, modify, and contribute.

## Getting Started

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/hanisntsolo/codeforces-lamp.git
    cd codeforces-lamp
    ```
2. **Obtain and setup environment variables for the container**
    ```bash
    Open docker-compose.yml and update these env variables.
      - CODEFORCES_API_KEY=${CODEFORCES_API_KEY}
      - CODEFORCES_API_SECRET=${CODEFORCES_API_SECRET}
      - TUYA_ACCESS_ID=${TUYA_ACCESS_ID}
      - TUYA_ACCESS_KEY=${TUYA_ACCESS_KEY}
      - TUYA_BULB_ID=${TUYA_BULB_ID}
    ```
3. **Build the Docker Image**:
    ```bash
    docker build -t codeforces-lamp .
    ```

4. **Run the Docker Container**:
    ```bash
    sh rebuild_and_run.sh
    ```

## Usage

Detailed usage instructions and examples can be found in the [documentation](./README.md).

## Contributing

Contributions are highly welcome! Please create a pull request for feature enhancements.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

For any questions or suggestions, feel free to open an issue or reach out via email at ds.pratap1997@gmail.com.
