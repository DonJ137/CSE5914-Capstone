const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

// Define the URL pattern for majors (1 to 161)
const base_url = "https://undergrad.osu.edu/majors-and-academics/majors/detail/";
const major_names = [];

// Function to scrape major names
async function scrapeMajors() {
    for (let major_id = 1; major_id <= 161; major_id++) {
        const url = base_url + major_id;

        try {
            const response = await axios.get(url);
            if (response.status === 200) {
                const $ = cheerio.load(response.data);
                const major_name = $(".col-md-6 h1").text().trim(); // Select <h1> within .col-md-6
                major_names.push(major_name);
            } else {
                console.error(`Failed to fetch data from ${url}`);
            }
        } catch (error) {
            console.error(`Error fetching data from ${url}:`, error);
        }
    }

    // Save the major_names array as a JSON file
    fs.writeFileSync('majors.json', JSON.stringify(major_names));
}

// Run the scraping
scrapeMajors()
