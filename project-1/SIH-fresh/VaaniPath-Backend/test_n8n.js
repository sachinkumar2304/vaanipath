async function test() {
    const username = "Gyanify";
    const password = "Gyanify123";
    const token = Buffer.from(`${username}:${password}`).toString('base64');

    const url = "https://zaiddd.app.n8n.cloud/webhook/8be78b34-dbc8-418a-83b0-044991ac14c2";

    console.log(`Testing URL: ${url}`);
    console.log(`Token: ${token}`);

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Basic ${token}`
            },
            body: JSON.stringify({
                "current-skills": "java,python",
                "goal": "SDE",
                "language": "english"
            })
        });

        console.log(`Status: ${response.status}`);
        const text = await response.text();
        console.log(`Response: ${text}`);

    } catch (error) {
        console.error("Error:", error);
    }
}

test();
