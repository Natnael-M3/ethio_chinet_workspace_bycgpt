import axios from "axios";

function AvailablePosts() {
  const takePost = async (postId) => {
    await axios.post(`/api/posts/${postId}/take/`);
    alert("Post taken");
  };

  return <button onClick={() => takePost(10)}>To Taken</button>;
}
