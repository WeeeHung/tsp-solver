const solverOptionsEl = document.getElementById("solver-options");
const formEl = document.getElementById("solve-form");
const submitButtonEl = document.getElementById("submit-button");
const locationsEl = document.getElementById("locations-input");
const regionEl = document.getElementById("region-input");
const resultsSectionEl = document.getElementById("results-section");
const resultsContainerEl = document.getElementById("results-container");

const solverOptionTemplate = document.getElementById("solver-option-template");
const resultCardTemplate = document.getElementById("result-card-template");

let cachedSolvers = [];

init();

async function init() {
    await loadSolvers();
    formEl.addEventListener("submit", handleSubmit);
}

async function loadSolvers() {
    solverOptionsEl.innerHTML = "<p>Loading solvers…</p>";

    try {
        const response = await fetch("/api/solvers");
        if (!response.ok) {
            throw new Error(`Failed to load solvers (${response.status})`);
        }
        const data = await response.json();
        cachedSolvers = data.solvers ?? [];
        renderSolverOptions(cachedSolvers);
    } catch (err) {
        solverOptionsEl.innerHTML = `<p class="error">Unable to load solvers: ${err.message}</p>`;
    }
}

function renderSolverOptions(solvers) {
    solverOptionsEl.innerHTML = "";

    const fragment = document.createDocumentFragment();
    const availableSolvers = solvers.filter((solver) => solver.available);

    solvers.forEach((solver) => {
        const node = solverOptionTemplate.content.cloneNode(true);
        const label = node.querySelector(".solver-option");
        const checkbox = node.querySelector('input[type="checkbox"]');
        const nameSpan = node.querySelector(".solver-name");
        const descriptionSpan = node.querySelector(".solver-description");

        checkbox.value = solver.slug;
        nameSpan.textContent = solver.name;
        descriptionSpan.textContent =
            solver.description || "No description available.";

        if (!solver.available) {
            label.classList.add("disabled");
            checkbox.disabled = true;
            descriptionSpan.textContent += " (Unavailable on this setup)";
        } else if (availableSolvers.length === 1) {
            checkbox.checked = true;
        }

        fragment.appendChild(node);
    });

    solverOptionsEl.appendChild(fragment);
}

function handleSubmit(event) {
    event.preventDefault();

    const locations = locationsEl.value
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean);

    if (locations.length < 2) {
        alert("Enter at least two locations.");
        return;
    }

    const selectedSolvers = Array.from(
        formEl.querySelectorAll('input[name="solver"]:checked')
    ).map((input) => input.value);

    if (selectedSolvers.length === 0) {
        alert("Select at least one solver.");
        return;
    }

    submitButtonEl.disabled = true;
    submitButtonEl.textContent = "Solving…";
    renderResultsPlaceholder("Hold tight! Fetching routes…");

    solveRequest({
        locations,
        solvers: selectedSolvers,
        region: regionEl.value.trim() || "sg",
    })
        .catch((err) => {
            renderResultsPlaceholder(
                `Something went wrong: ${err.message}. Please try again.`
            );
        })
        .finally(() => {
            submitButtonEl.disabled = false;
            submitButtonEl.textContent = "Solve Route";
        });
}

async function solveRequest(payload) {
    const response = await fetch("/api/solve", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        const message =
            detail?.detail ??
            `Server error (${response.status}) – please check the console logs.`;
        throw new Error(message);
    }

    const data = await response.json();
    renderResults(data.results ?? []);
}

function renderResultsPlaceholder(message) {
    resultsSectionEl.classList.remove("hidden");
    resultsContainerEl.innerHTML = `<p>${message}</p>`;
}

function renderResults(results) {
    if (!Array.isArray(results) || results.length === 0) {
        renderResultsPlaceholder("No results to show yet.");
        return;
    }

    const fragment = document.createDocumentFragment();

    results.forEach((result, index) => {
        const node = resultCardTemplate.content.cloneNode(true);
        const titleEl = node.querySelector(".solver-title");
        const metaEl = node.querySelector(".solver-meta");
        const detailsEl = node.querySelector(".route-details");
        const toggleButton = node.querySelector(".toggle-map");
        const shareLink = node.querySelector(".share-link");
        const mapContainer = node.querySelector(".map-container");
        const mapFrame = node.querySelector(".map-frame");

        titleEl.textContent = result.solver;

        metaEl.textContent = `${result.total_distance_km.toFixed(
            2
        )} km • ${result.solve_time_s.toFixed(3)} s • ${
            result.num_locations
        } stops`;

        detailsEl.innerHTML = buildRouteList(result.route);

        if (!result.map_embed_url) {
            toggleButton.disabled = true;
            toggleButton.textContent = "Map unavailable";
        } else {
            mapFrame.src = result.map_embed_url;
            toggleButton.addEventListener("click", () => {
                mapContainer.classList.toggle("hidden");
                toggleButton.textContent = mapContainer.classList.contains(
                    "hidden"
                )
                    ? "Show Route Map"
                    : "Hide Route Map";
            });

            if (index === 0) {
                mapContainer.classList.remove("hidden");
                toggleButton.textContent = "Hide Route Map";
            }
        }

        if (result.map_share_url) {
            shareLink.href = result.map_share_url;
        } else {
            shareLink.classList.add("disabled");
            shareLink.removeAttribute("href");
        }

        fragment.appendChild(node);
    });

    resultsSectionEl.classList.remove("hidden");
    resultsContainerEl.innerHTML = "";
    resultsContainerEl.appendChild(fragment);
}

function buildRouteList(route) {
    if (!Array.isArray(route) || route.length === 0) {
        return "<p>No route details available.</p>";
    }

    const items = route
        .map((stop, index) => {
            const label =
                stop.formatted_address && stop.formatted_address !== stop.name
                    ? `${stop.name} <small>(${stop.formatted_address})</small>`
                    : stop.name;
            if (index === 0) {
                return `<li><strong>Start:</strong> ${label}</li>`;
            }
            if (index === route.length - 1) {
                return `<li><strong>End:</strong> ${label}</li>`;
            }
            return `<li>${label}</li>`;
        })
        .join("");

    return `<p>Visit order:</p><ol>${items}</ol>`;
}

