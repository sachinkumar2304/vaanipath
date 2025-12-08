async function test() {
    const url = "https://zaiddd.app.n8n.cloud/webhook/8be78b34-dbc8-418a-83b0-044991ac14c2";

    console.log(`Testing URL without Auth: ${url}`);

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
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
