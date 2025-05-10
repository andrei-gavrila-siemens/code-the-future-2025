'use server';

const url = "https://4ce5-86-124-190-69.ngrok-free.app"

export async function fetchCubes(){
  try {
    const response = await fetch(url + "/cubes");
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch cubes:", error);
    return null;
  }
}

export async function fetchMostWanted() {
  try {
    const response = await fetch(url + "/top-cubes");
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch cubes:", error);
    return null;
  }
}

export async function sendOrder(cart){
  await fetch(url + '/cubes', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(cart)
  });
}